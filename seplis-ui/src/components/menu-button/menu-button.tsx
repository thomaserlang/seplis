import { Button, Menu } from '@mantine/core'
import { CaretDownIcon } from '@phosphor-icons/react'
import { NavLink } from 'react-router-dom'
import classes from './menu-button.module.css'

interface Props {
    label: string
    to: string
    end?: boolean
    items?: Props[]
}

export function MenuButton(props: Props) {
    if (props.items) {
        return (
            <Menu shadow="md" width={200}>
                <Menu.Target>
                    <Button
                        size="compact-md"
                        variant="subtle"
                        className={classes.root}
                        rightSection={<CaretDownIcon />}
                    >
                        {props.label}
                    </Button>
                </Menu.Target>
                <Menu.Dropdown>
                    {props.items.map((item) => (
                        <Menu.Item
                            key={item.to}
                            component={NavLink}
                            to={item.to}
                        >
                            {item.label}
                        </Menu.Item>
                    ))}
                </Menu.Dropdown>
            </Menu>
        )
    }

    return (
        <Button
            size="compact-md"
            component={NavLink}
            variant="subtle"
            className={classes.root}
            {...props}
        >
            {props.label}
        </Button>
    )
}
